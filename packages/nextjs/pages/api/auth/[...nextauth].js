import NextAuth from "next-auth";
import GitHubProvider from "next-auth/providers/github";

export default NextAuth({
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID || "Ov23ctVKc9GhCsln3xnr",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "ed8fad8565fcf9fc8454b0472a182d1437294189",
    }),
  ],
  callbacks: {
    async session({ session, token, user }) {
      session.user.id = token.sub;
      session.user.profile = token.profile;
      return session;
    },
    async jwt({ token, user, account, profile }) {
      if (account && user) {
        token.profile = profile;
      }
      return token;
    },
  },
});
