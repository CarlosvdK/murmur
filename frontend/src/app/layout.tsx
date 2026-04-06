import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Murmur -- Customer Simulation for Small Businesses",
  description:
    "Ask any question about your customers. Get honest, nuanced feedback from simulated customers tailored to your business.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body
        className="min-h-screen antialiased"
        style={{ background: "#F5F3EF", color: "#000000", fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif" }}
      >
        <main>{children}</main>
      </body>
    </html>
  );
}
