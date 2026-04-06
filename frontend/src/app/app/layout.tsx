import TopNav from "@/components/shell/TopNav";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen flex-col" style={{ background: "#F5F3EF" }}>
      <TopNav />
      <div className="flex-1 overflow-hidden">{children}</div>
    </div>
  );
}
