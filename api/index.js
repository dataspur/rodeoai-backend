import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method === "GET" && req.url === "/health") {
    return res.status(200).json({ status: "RodeoAI backend live" });
  }

  if (req.method === "POST" && (req.url === "/chat" || req.url === "/chat/")) {
    const { message, model } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }

    try {
      const response = await client.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 300,
        system: "You are an expert rodeo coach and instructor. Provide expert advice on roping techniques, horse training, competition strategies, and all aspects of professional rodeo. Be concise but informative.",
        messages: [{ role: "user", content: message }],
      });

      return res.status(200).json({
        reply: response.content[0].text,
        model: model || "claude",
      });
    } catch (error) {
      return res.status(500).json({ error: `Error: ${error.message}` });
    }
  }

  if (req.method === "POST" && req.url === "/analytics/log") {
    return res.status(200).json({ status: "ok", logged: true });
  }

  return res.status(404).json({ error: "Endpoint not found" });
}
