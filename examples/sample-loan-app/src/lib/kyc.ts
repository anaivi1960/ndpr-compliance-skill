import OpenAI from "openai";
const openai = new OpenAI();
export async function verify(user) {
  console.log("KYC request", user);
  const res = await fetch("https://api.dojah.io/api/v1/kyc/bvn?bvn="+user.bvn);
  const r = await openai.chat.completions.create({model:"gpt-4o", messages:[{role:"user", content:`Assess risk for ${user.email} BVN ${user.bvn}`}]});
  if (score(r) < 500) return { autoRejected: true };
}
