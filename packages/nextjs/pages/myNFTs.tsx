import type { NextPage } from "next";
import { signIn, signOut, useSession } from "next-auth/react";
import { useAccount } from "wagmi";
import { MetaHeader } from "~~/components/MetaHeader";
import { RainbowKitCustomConnectButton } from "~~/components/scaffold-eth";
import { MyHoldings } from "~~/components/simpleNFT";
import { useScaffoldContractRead, useScaffoldContractWrite } from "~~/hooks/scaffold-eth";
import { useUserNFTs } from "~~/hooks/scaffold-eth/useUserNFTs";
import { notification } from "~~/utils/scaffold-eth";
import { ipfsClient } from "~~/utils/simpleNFT";

const MyNFTs: NextPage = () => {
  const { nfts, isLoading } = useUserNFTs();
  const { data: session } = useSession();

  const { address: connectedAddress, isConnected, isConnecting } = useAccount();

  const { writeAsync: mintItem } = useScaffoldContractWrite({
    contractName: "YourCollectible",
    functionName: "mintItem",
    args: [connectedAddress, ""],
  });

  const { data: tokenIdCounter } = useScaffoldContractRead({
    contractName: "YourCollectible",
    functionName: "tokenIdCounter",
    watch: true,
    cacheOnBlock: true,
  });

  const handleMintItem = async () => {
    if (!session) return;
    // circle back to the zero item if we've reached the end of the array
    if (tokenIdCounter === undefined) return;

    const currentTokenMetaData = {
      description: "My GitSBT",
      external_url: session.user.profile.html_url, // github link
      image: session.user.image, // github avatar
      name: session.user.profile.login, // github nick
      attributes: [
        {
          trait_type: "SubmissionCount",
          value: 0,
        },
        {
          trait_type: "HackathonCount",
          value: 0,
        },
        {
          trait_type: "VictoryCount",
          value: 0,
        },
      ],
    };

    const notificationId = notification.loading("Uploading to IPFS");
    try {
      const uploadedItem = await ipfsClient.add(JSON.stringify(currentTokenMetaData));

      // First remove previous loading notification and then show success notification
      notification.remove(notificationId);
      notification.success("Metadata uploaded to IPFS");

      await mintItem({
        args: [connectedAddress, uploadedItem.path],
      });
    } catch (error) {
      notification.remove(notificationId);
      console.error(error);
    }
  };

  return (
    <>
      <MetaHeader />
      <div className="flex items-center flex-col pt-10">
        <div className="px-5">
          <h1 className="text-center mb-8">
            <span className="block text-4xl font-bold">My SBT</span>
          </h1>
        </div>
      </div>
      <div className="flex justify-center mb-8">
        {session ? (
          <div className="flex justify-center items-center gap-4">
            {session?.user?.name}
            <button className="btn btn-secondary" onClick={() => signOut()}>
              Sign out
            </button>
          </div>
        ) : (
          <button className="btn btn-secondary" onClick={() => signIn()}>
            Connect your GitHub and mint SBT
          </button>
        )}
      </div>
      <div className="flex justify-center">
        {!isConnected || isConnecting ? (
          <RainbowKitCustomConnectButton />
        ) : session && !isLoading && nfts.length === 0 ? (
          <button className="btn btn-secondary" onClick={handleMintItem}>
            Mint SBT
          </button>
        ) : null}
      </div>
      <MyHoldings />
    </>
  );
};

export default MyNFTs;
