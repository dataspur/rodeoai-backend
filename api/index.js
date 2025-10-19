import fetch from "node-fetch";

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method === "POST" && (req.url === "/api/chat" || req.url === "/api/chat/")) {
    const { message, model } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Message is required" });
    }

    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
        },
        body: JSON.stringify({
          model: "gpt-4",
          messages: [
            {
              role: "system",
              content: "You are an expert rodeo coach. Provide concise, expert advice on roping, horse training, and rodeo strategy.",
            },
            { role: "user", content: message },
          ],
          max_tokens: 300,
        }),
      });

      const data = await response.json();
      return res.status(200).json({
        reply: data.choices[0].message.content,
        model: model || "gpt-4",
      });
    } catch (error) {
      return res.status(500).json({ error: `Error: ${error.message}` });
    }
  }

  return res.status(404).json({ error: "Endpoint not found" });
}
