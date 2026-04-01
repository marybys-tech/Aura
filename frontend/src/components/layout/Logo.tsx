interface LogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
}

const SIZES = {
  sm: { orb: "h-5 w-5", text: "text-base", blur: "8px" },
  md: { orb: "h-6 w-6", text: "text-lg", blur: "10px" },
  lg: { orb: "h-8 w-8", text: "text-2xl", blur: "14px" },
};

export default function Logo({ size = "md", showText = true }: LogoProps) {
  const s = SIZES[size];

  return (
    <div className="flex items-center gap-2.5">
      <div className={`${s.orb} relative shrink-0 rounded-full`}>
        {/* Outer glow */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 0deg, #8B5CF6, #0EA5E9, #10B981, #F59E0B, #F97316, #EC4899, #8B5CF6)",
            filter: `blur(${s.blur})`,
            opacity: 0.7,
            transform: "scale(1.4)",
          }}
        />
        {/* Solid orb */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: "conic-gradient(from 120deg, #8B5CF6, #10B981, #EC4899, #0EA5E9, #8B5CF6)",
            boxShadow: "0 0 8px rgba(139,92,246,0.4)",
          }}
        />
      </div>
      {showText && (
        <span className={`${s.text} font-bold tracking-tight`}>Aura</span>
      )}
    </div>
  );
}
