import TopNav from "@/components/shell/TopNav";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <style>{`
        .app-scaled * {
          font-size-adjust: none;
        }
        .app-scaled .text-\\[9px\\] { font-size: 14px !important; }
        .app-scaled .text-\\[10px\\] { font-size: 15px !important; }
        .app-scaled .text-\\[11px\\] { font-size: 17px !important; }
        .app-scaled .text-xs { font-size: 18px !important; line-height: 1.4 !important; }
        .app-scaled .text-sm { font-size: 21px !important; line-height: 1.4 !important; }
        .app-scaled .text-base { font-size: 24px !important; line-height: 1.4 !important; }
        .app-scaled .text-lg { font-size: 27px !important; line-height: 1.3 !important; }
        .app-scaled .text-xl { font-size: 30px !important; line-height: 1.3 !important; }
        .app-scaled .text-2xl { font-size: 36px !important; line-height: 1.2 !important; }
        .app-scaled .text-3xl { font-size: 45px !important; line-height: 1.2 !important; }
        .app-scaled .text-4xl { font-size: 54px !important; line-height: 1.1 !important; }
        .app-scaled .text-5xl { font-size: 72px !important; line-height: 1.1 !important; }
        .app-scaled input, .app-scaled textarea, .app-scaled select, .app-scaled button {
          font-size: inherit !important;
        }
        .app-scaled input::placeholder, .app-scaled textarea::placeholder {
          font-size: inherit !important;
        }
      `}</style>
      <div className="app-scaled flex h-screen flex-col" style={{ background: "#F5F3EF" }}>
        <TopNav />
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </>
  );
}
