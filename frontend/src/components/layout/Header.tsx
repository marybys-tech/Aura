import { Moon, Sun, Bell } from "lucide-react";
import { useThemeStore } from "@/stores/theme";
import { useCurrentUser, useLogout } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Logo from "./Logo";

export default function Header() {
  const { theme, toggle } = useThemeStore();
  const { data: user } = useCurrentUser();
  const logout = useLogout();

  return (
    <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center justify-between border-b border-border bg-background/80 px-4 backdrop-blur-sm lg:px-6">
      <div className="lg:hidden">
        <Logo size="sm" />
      </div>

      <div className="hidden lg:block" />

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="h-9 w-9 text-muted-foreground" onClick={toggle}>
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>

        <Button variant="ghost" size="icon" className="h-9 w-9 text-muted-foreground">
          <Bell className="h-4 w-4" />
        </Button>

        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger className="flex h-9 items-center gap-2 rounded-md px-2 text-sm font-medium hover:bg-accent focus:outline-none">
              <Avatar className="h-7 w-7">
                <AvatarImage src={user.avatar_url ?? undefined} />
                <AvatarFallback className="text-xs">{user.display_name[0]}</AvatarFallback>
              </Avatar>
              <span className="hidden lg:inline">{user.display_name}</span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => logout.mutate()}>
                Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </header>
  );
}
