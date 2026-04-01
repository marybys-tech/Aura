import { Link, useMatchRoute } from "@tanstack/react-router";
import type { LucideIcon } from "lucide-react";
import Logo from "./Logo";
import { NAV_ITEMS } from "@/lib/nav-items";
import { useSidebarStore } from "@/stores/sidebar";

export default function Sidebar() {
  const collapsed = useSidebarStore((s) => s.collapsed);

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 hidden flex-col border-r border-border bg-sidebar transition-all duration-200 lg:flex ${
        collapsed ? "w-16" : "w-52"
      }`}
    >
      <div className={`flex items-center pb-6 pt-4 ${collapsed ? "justify-center px-2" : "px-4"}`}>
        <Logo size={collapsed ? "sm" : "md"} showText={!collapsed} />
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-2">
        {NAV_ITEMS.map((item) => (
          <SidebarLink key={item.to} collapsed={collapsed} {...item} />
        ))}
      </nav>
    </aside>
  );
}

function SidebarLink({ to, label, icon: Icon, collapsed }: { to: string; label: string; icon: LucideIcon; collapsed: boolean }) {
  const matchRoute = useMatchRoute();
  const isActive = !!matchRoute({ to, fuzzy: to !== "/" });

  return (
    <Link
      to={to}
      className={`flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
        collapsed ? "justify-center" : "gap-3"
      } ${
        isActive
          ? "bg-primary/10 text-primary"
          : "text-muted-foreground hover:bg-accent hover:text-foreground"
      }`}
      title={collapsed ? label : undefined}
    >
      <Icon className="h-4 w-4 shrink-0" />
      {!collapsed && label}
    </Link>
  );
}
