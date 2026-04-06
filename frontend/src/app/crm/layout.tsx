import CRMSidebar from "@/components/crm/CRMSidebar";

export default function CRMLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <CRMSidebar />
      <main className="flex-1 overflow-y-auto bg-[#F5F3EF] p-8">
        {children}
      </main>
    </div>
  );
}
