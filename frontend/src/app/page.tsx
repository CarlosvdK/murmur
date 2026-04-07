import Navigation from "@/components/landing2/Navigation";
import HeroDemoCard from "@/components/landing2/HeroDemoCard";
import TrustBar from "@/components/landing2/TrustBar";
import ProblemSection from "@/components/landing2/ProblemSection";
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

      {/* HERO -- bird murmuration + gradient accents on eggshell */}
      <section className="relative min-h-[90vh] overflow-hidden px-8 pb-20 pt-32 lg:px-16 xl:px-24">
        <Murmuration />

        {/* Soft glow blob */}
        <div
          className="pointer-events-none absolute left-1/2 top-0 -translate-x-1/2"
          style={{
            width: 900,
            height: 500,
            background: "radial-gradient(ellipse, rgba(68,140,253,0.08) 0%, rgba(255,141,228,0.04) 40%, transparent 70%)",
          }}
        />

        <div className="relative z-10 grid gap-12 lg:grid-cols-2 lg:items-center">
          <div>
            <SectionReveal>
              <span className="mb-6 inline-flex items-center gap-2 rounded-full bg-brand-orange px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.12em] text-white">
                Customer intelligence for small businesses
              </span>
            </SectionReveal>

            <SectionReveal delay={0.1}>
              <h1 className="mb-8 text-[clamp(48px,8vw,96px)] font-black leading-[0.95] tracking-[-0.03em] text-black">
                Know how your
                <br />
                customers will{" "}
                <span className="text-brand-orange">react.</span>
              </h1>
            </SectionReveal>

            <SectionReveal delay={0.2}>
              <p className="mb-10 max-w-lg text-xl leading-relaxed text-gray-500">
                Murmur builds a real simulation of your customer base and asks
                them your question. Honest feedback from people who actually
                know your business.
              </p>
            </SectionReveal>

            <SectionReveal delay={0.3}>
              <div className="flex flex-wrap items-center gap-4">
                <a
                  href="/login"
                  className="rounded-full bg-black px-8 py-3.5 text-sm font-bold text-white transition-all hover:opacity-80 hover:scale-[1.02]"
                >
                  Sign in
                </a>
                <a
                  href="/signup"
                  className="rounded-full border border-gray-300 bg-white px-8 py-3.5 text-sm font-medium text-black transition-colors hover:border-gray-500"
                >
                  Create an account
                </a>
              </div>
            </SectionReveal>

            <SectionReveal delay={0.4}>
              <p className="mt-10 text-xs text-gray-400">
                Trusted by restaurant owners, barbers, and shop owners in 15
                cities
              </p>
            </SectionReveal>
          </div>

          <SectionReveal delay={0.3}>
            <HeroDemoCard />
          </SectionReveal>
        </div>
      </section>

      {/* TRUST BAR -- vivid gradient band */}
      <TrustBar />

      <ProblemSection />
      <HowItWorks />

      <div id="demo">
        <LiveDemo />
      </div>

      <EngineSection />
      <UseCases />
      <AccuracySection />
      <Testimonials />

      {/* FINAL CTA -- gradient band */}
      <FinalCTA />
    </div>
  );
}
