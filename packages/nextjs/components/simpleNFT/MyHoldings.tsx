import { Spinner } from "../Spinner";
import { NFTCard } from "./NFTCard";
import { useUserNFTs } from "~~/hooks/scaffold-eth/useUserNFTs";
import { NFTMetaData } from "~~/utils/simpleNFT";

export interface Collectible extends Partial<NFTMetaData> {
  id: number;
  uri: string;
  owner: string;
}

export const MyHoldings = () => {
  const { nfts, isLoading } = useUserNFTs();

  if (isLoading)
    return (
      <div className="flex justify-center items-center mt-10">
        <Spinner width="75" height="75" />
      </div>
    );

  return (
    <>
      {nfts.length === 0 ? (
        <div className="flex justify-center items-center mt-10">
          <div className="text-2xl text-primary-content">No NFTs found</div>
        </div>
      ) : (
        <div className="flex flex-wrap gap-4 my-8 px-5 justify-center">
          {nfts.map(item => (
            <NFTCard nft={item} key={item.id} />
          ))}
        </div>
      )}
    </>
  );
};
