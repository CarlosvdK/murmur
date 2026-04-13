"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { listBusinesses, listSimulations, listContacts } from "@/lib/api";
import Tutorial from "@/components/shell/Tutorial";

export default function AppHome() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [showTutorial, setShowTutorial] = useState(false);
  const [stats, setStats] = useState({ simulations: 0, customers: 0, vendors: 0, twins: 0 });

  const fetchStats = () => {
    Promise.all([
      listSimulations().catch(() => []),
      listContacts({ contact_type: "customer" }).catch(() => []),
      listContacts({ contact_type: "vendor" }).catch(() => []),
    ]).then(([sims, customers, vendors]) => {
      setStats({
        simulations: sims.length,
        customers: customers.length,
        vendors: vendors.length,
        twins: [...customers, ...vendors].filter((c) => c.has_twin).length,
      });
    });
  };

  useEffect(() => {
    listBusinesses()
      .then((businesses) => {
        if (businesses.length === 0) {
          router.replace("/onboarding");
        } else {
          setReady(true);
          fetchStats();
          // Show tutorial on first visit
          if (!localStorage.getItem("murmur_tutorial_seen")) {
            setTimeout(() => setShowTutorial(true), 500);
          }
          const interval = setInterval(fetchStats, 30000);
          return () => clearInterval(interval);
        }
      })
      .catch(() => {
        router.replace("/onboarding");
      });
  }, [router]);

  if (!ready) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  const cards = [
    {
      href: "/app/simulate",
      image: "/simulation.png",
      label: "Simulate",
      tutId: "card-simulate",
      color: "brand-blue",
      borderHover: "hover:border-brand-blue",
      desc: "Generate a diverse panel of AI customers tailored to your business and ask them any question. Get honest reactions, sentiment analysis, and a go/no-go recommendation backed by behavioural science.",
      cta: "Run a simulation",
    },
    {
      href: "/app/customers",
      image: "/customer_twin.png",
      label: "Customer Twins",
      tutId: "card-customers",
      color: "brand-orange",
      borderHover: "hover:border-brand-orange",
      desc: "Build a digital twin of each high-value customer from your real conversations. Upload WhatsApp, email, or meeting notes and ask the twin how they would react to pricing changes, new offerings, or difficult conversations.",
      cta: "Manage customers",
    },
    {
      href: "/app/vendors",
      image: "/vendor_twin.png",
      label: "Vendor Twins",
      tutId: "card-vendors",
      color: "brand-pink",
      borderHover: "hover:border-brand-pink",
      desc: "Create digital twins of your suppliers and partners from correspondence history. Predict their negotiation style, anticipate counter-offers, and prepare for every meeting with data-backed intelligence.",
      cta: "Manage vendors",
    },
  ];

  return (
    <>
    {showTutorial && (
      <Tutorial onComplete={() => {
        setShowTutorial(false);
        localStorage.setItem("murmur_tutorial_seen", "true");
      }} />
    )}
    <div className="overflow-y-auto p-8 lg:p-12">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-1 text-3xl font-bold text-black">
          Welcome to Murmur
        </h1>
        <p className="mb-10 text-lg text-gray-500">
          What would you like to do?
        </p>

        {/* Stats bar */}
        <div className="mb-10 flex gap-8">
          {[
            [stats.simulations, "Simulations"],
            [stats.customers, "Customers"],
            [stats.vendors, "Vendors"],
            [stats.twins, "Active twins"],
          ].map(([val, label], i) => (
            <div key={label as string} className="flex items-center gap-8">
              <div>
                <p className="text-2xl font-bold text-black">{val}</p>
                <p className="text-xs text-gray-400">{label}</p>
              </div>
              {i < 3 && <div className="h-8 w-px bg-[#E5E2DC]" />}
            </div>
          ))}
        </div>

        {/* Feature cards with images */}
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {cards.map((card) => (
            <a
              key={card.label}
              data-tut={card.tutId}
              href={card.href}
              className={`group flex flex-col overflow-hidden rounded-2xl border border-[#E5E2DC] bg-white transition-all hover:-translate-y-1 ${card.borderHover} hover:shadow-lg`}
            >
              {/* Image */}
              <div className="relative h-56 w-full overflow-hidden bg-gray-100">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={card.image}
                  alt={card.label}
                  className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              </div>

              {/* Content */}
              <div className="flex flex-1 flex-col p-6">
                <h3 className="mb-2 text-lg font-bold text-black">{card.label}</h3>
                <p className="mb-4 flex-1 text-sm leading-relaxed text-gray-500">
                  {card.desc}
                </p>
                <span className={`flex items-center gap-1 text-sm font-medium text-${card.color}`}>
                  {card.cta} <ArrowRight className="h-4 w-4" />
                </span>
              </div>
            </a>
          ))}
        </div>

        {/* Recent activity section */}
        <div className="mt-12">
          <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-gray-400">Recent activity</h2>
          <div className="rounded-xl border border-[#E5E2DC] bg-white p-8 text-center">
            <p className="text-sm text-gray-400">Run your first simulation to see activity here.</p>
            <a href="/app/simulate" className="mt-3 inline-block text-sm font-medium text-brand-blue hover:underline">
              Go to Simulate
            </a>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
