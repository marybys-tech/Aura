import { Link, useMatchRoute } from "@tanstack/react-router";
import { LayoutDashboard, ListChecks } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import Logo from "./Logo";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/habits", label: "Habits", icon: ListChecks },
] as const;

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-56 flex-col border-r border-border bg-sidebar p-4 lg:flex">
      <div className="px-3 pb-8 pt-2">
        <Logo size="md" />
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} {...item} />
        ))}
      </nav>
    </aside>
  );
}

function SidebarLink({ to, label, icon: Icon }: { to: string; label: string; icon: LucideIcon }) {
  const matchRoute = useMatchRoute();
  const isActive = !!matchRoute({ to, fuzzy: to !== "/" });

  return (
    <Link
      to={to}
      className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
        isActive
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-accent hover:text-foreground"
      }`}
    >
      <Icon className="h-4 w-4" />
      {label}
    </Link>
  );
}
