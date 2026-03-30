interface LogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
}

const SIZES = {
  sm: { orb: "h-5 w-5", text: "text-base", blur: "8px", spread: "6px" },
  md: { orb: "h-6 w-6", text: "text-lg", blur: "10px", spread: "8px" },
  lg: { orb: "h-8 w-8", text: "text-2xl", blur: "14px", spread: "10px" },
};

export default function Logo({ size = "md", showText = true }: LogoProps) {
  const s = SIZES[size];

  return (
    <div className="flex items-center gap-2.5">
      <div className={`${s.orb} relative shrink-0 rounded-full`}>
        {/* Multi-color aura orb */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 0deg, #A78BFA, #38BDF8, #34D399, #FBBF24, #FB923C, #F472B6, #A78BFA)",
            filter: `blur(${s.blur})`,
            opacity: 0.7,
            transform: "scale(1.4)",
          }}
        />
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 120deg, #A78BFA, #34D399, #F472B6, #38BDF8, #A78BFA)",
            boxShadow: `0 0 ${s.spread} rgba(167,139,250,0.4)`,
          }}
        />
        <div className="absolute inset-[2px] rounded-full bg-background/30 backdrop-blur-sm" />
      </div>
      {showText && (
        <span className={`${s.text} font-bold tracking-tight`}>Aura</span>
      )}
    </div>
  );
}
