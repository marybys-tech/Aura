import { Link, useMatchRoute } from "@tanstack/react-router";
import type { LucideIcon } from "lucide-react";
import { NAV_ITEMS } from "@/lib/nav-items";

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 flex border-t border-border bg-card/95 backdrop-blur-sm lg:hidden">
      {NAV_ITEMS.map((item) => (
        <BottomNavLink key={item.to} {...item} />
      ))}
    </nav>
  );
}

function BottomNavLink({ to, label, icon: Icon }: { to: string; label: string; icon: LucideIcon }) {
  const matchRoute = useMatchRoute();
  const isActive = !!matchRoute({ to, fuzzy: to !== "/" });

  return (
    <Link
      to={to}
      className={`flex flex-1 flex-col items-center gap-1 py-3 text-[11px] font-medium transition-colors ${
        isActive ? "text-primary" : "text-muted-foreground"
      }`}
    >
      <Icon className="h-5 w-5" />
      {label}
    </Link>
  );
}
