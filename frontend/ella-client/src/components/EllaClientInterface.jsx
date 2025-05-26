import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Mic, Send } from "lucide-react";

export default function EllaClientInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { sender: "user", text: input };
    setMessages([...messages, userMessage]);
    setInput("");
    setLoading(true);

    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });

    const data = await response.json();
    const botMessage = { sender: "ella", text: data.response };
    setMessages((prev) => [...prev, botMessage]);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-white p-4 flex flex-col max-w-2xl mx-auto">
      <h1 className="text-xl font-semibold mb-2">Ella</h1>
      <div className="flex-1 space-y-2 overflow-auto border rounded p-2 bg-gray-50">
        {messages.map((msg, i) => (
          <Card key={i} className={msg.sender === "ella" ? "bg-blue-50" : "bg-white"}>
            <CardContent className="p-3">
              <span className="font-bold mr-2">{msg.sender === "ella" ? "Ella" : "You"}:</span>
              <span>{msg.text}</span>
            </CardContent>
          </Card>
        ))}
        {loading && <div className="italic text-sm">Ella is typing...</div>}
      </div>
      <div className="mt-4 flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1"
        />
        <Button onClick={sendMessage}><Send className="w-4 h-4" /></Button>
        <Button variant="ghost"><Mic className="w-4 h-4" /></Button>
      </div>
    </div>
  );
}
