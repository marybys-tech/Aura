import { createRouter, createRoute, createRootRoute, redirect, Outlet } from "@tanstack/react-router";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import BottomNav from "@/components/layout/BottomNav";
import MasterPopup from "@/components/master/MasterPopup";
import DevPanel from "@/components/dashboard/DevPanel";
import LoginPage from "@/pages/LoginPage";
import OAuthCallbackPage from "@/pages/OAuthCallbackPage";
import DashboardPage from "@/pages/DashboardPage";
import HabitsPage from "@/pages/HabitsPage";

// Root
const rootRoute = createRootRoute({
  component: () => <Outlet />,
});

// Public routes
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/login",
  component: LoginPage,
});

const oauthCallbackRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/oauth/$provider/callback",
  component: OAuthCallbackPage,
});

// Authenticated layout
const authenticatedRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: "authenticated",
  beforeLoad: () => {
    if (!localStorage.getItem("access_token")) {
      throw redirect({ to: "/login" });
    }
  },
  component: function AuthLayout() {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar />
        <div className="flex flex-1 flex-col lg:ml-56">
          <Header />
          <main className="flex-1 overflow-y-auto pb-20 lg:pb-0">
            <Outlet />
          </main>
          <BottomNav />
        </div>
        <MasterPopup />
        <DevPanel />
      </div>
    );
  },
});

const dashboardRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: "/",
  component: DashboardPage,
});

const habitsRoute = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: "/habits",
  component: HabitsPage,
});

// Tree
const routeTree = rootRoute.addChildren([
  loginRoute,
  oauthCallbackRoute,
  authenticatedRoute.addChildren([dashboardRoute, habitsRoute]),
]);

export const router = createRouter({
  routeTree,
  defaultNotFoundComponent: () => (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-muted-foreground">Page not found</p>
    </div>
  ),
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
