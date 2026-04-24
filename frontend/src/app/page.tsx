import Navigation from "@/components/landing2/Navigation";
import RotatingWord from "@/components/landing2/RotatingWord";
import HeroDemoCard from "@/components/landing2/HeroDemoCard";
import TrustBar from "@/components/landing2/TrustBar";
import ProblemSection from "@/components/landing2/ProblemSection";
import ProductPillars from "@/components/landing2/ProductPillars";
import HowItWorks from "@/components/landing2/HowItWorks";
import LiveDemo from "@/components/landing2/LiveDemo";
import EngineSection from "@/components/landing2/EngineSection";
import UseCases from "@/components/landing2/UseCases";
import AccuracySection from "@/components/landing2/AccuracySection";
import Testimonials from "@/components/landing2/Testimonials";
import FinalCTA from "@/components/landing2/FinalCTA";
import SectionReveal from "@/components/landing2/SectionReveal";
import Murmuration from "@/components/landing2/Murmuration";

export default function Home() {
  return (
    <div className="bg-[#F5F3EF]">
      <Navigation />

      {/* HERO -- eggshell */}
      <section className="relative min-h-[90vh] overflow-hidden px-6 pb-20 pt-32 lg:px-8 xl:px-12 2xl:px-16">
        <Murmuration />
        <div
          className="pointer-events-none absolute left-1/2 top-0 -translate-x-1/2"
          style={{
            width: 900,
            height: 500,
            background: "radial-gradient(ellipse, rgba(68,140,253,0.08) 0%, rgba(255,141,228,0.04) 40%, transparent 70%)",
          }}
        />
        <div className="relative z-10 mx-auto grid max-w-[1800px] gap-16 lg:grid-cols-[1.05fr_1fr] lg:items-center xl:gap-24">
          <div>
            <SectionReveal>
              <span className="mb-6 inline-flex items-center gap-2 rounded-full bg-brand-orange px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.12em] text-white">
                The new age of customer intelligence
              </span>
            </SectionReveal>
            <SectionReveal delay={0.1}>
              <h1 className="mb-8 text-[clamp(52px,8.5vw,120px)] font-black leading-[0.95] tracking-[-0.03em] text-black">
                Your customers,
                <br />
                <RotatingWord />
              </h1>
            </SectionReveal>
            <SectionReveal delay={0.2}>
              <p className="mb-6 max-w-2xl text-2xl leading-relaxed text-gray-500">
                Murmur is the CRM that thinks. Run a full customer simulation
                before making any business decision. Build digital twins of your
                most important customers and vendors from your real conversations.
              </p>
              <p className="mb-10 max-w-2xl text-lg leading-relaxed text-gray-400">
                Powered by behavioural science, cultural psychology, and live market
                intelligence, not guesswork.
              </p>
            </SectionReveal>
            <SectionReveal delay={0.3}>
              <div className="flex flex-wrap items-center gap-4">
                <a href="/login" className="rounded-full bg-black px-8 py-3.5 text-sm font-bold text-white transition-all hover:opacity-80 hover:scale-[1.02]">
                  Sign in
                </a>
                <a href="/signup" className="rounded-full border border-gray-300 bg-white px-8 py-3.5 text-sm font-medium text-black transition-colors hover:border-gray-500">
                  Create an account
                </a>
              </div>
            </SectionReveal>
            <SectionReveal delay={0.4}>
              <p className="mt-10 text-xs text-gray-400">
                No credit card required. Your first simulation is free.
              </p>
            </SectionReveal>
          </div>
          <SectionReveal delay={0.3}>
            <HeroDemoCard />
          </SectionReveal>
        </div>
      </section>

      {/* TRUST BAR -- gradient */}
      <TrustBar />

      {/* PROBLEM -- white */}
      <ProblemSection />

      {/* PRODUCT PILLARS -- eggshell */}
      <ProductPillars />

      {/* HOW IT WORKS -- white */}
      <HowItWorks />

      {/* LIVE DEMO -- white (handled internally) */}
      <div id="demo">
        <LiveDemo />
      </div>

      {/* ENGINE -- eggshell */}
      <EngineSection />

      {/* USE CASES -- white */}
      <UseCases />

      {/* ACCURACY -- eggshell */}
      <AccuracySection />

      {/* TESTIMONIALS -- white */}
      <Testimonials />

      {/* FINAL CTA -- gradient */}
      <FinalCTA />
    </div>
  );
}
