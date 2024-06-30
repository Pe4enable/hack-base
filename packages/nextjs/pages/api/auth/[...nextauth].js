import NextAuth from "next-auth";
import GitHubProvider from "next-auth/providers/github";

export default NextAuth({
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
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
