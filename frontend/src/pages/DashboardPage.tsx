import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import TodayView from "@/components/dashboard/TodayView";
import WeekView from "@/components/dashboard/WeekView";
import MonthView from "@/components/dashboard/MonthView";

export default function DashboardPage() {
  const today = new Date();
  const dateStr = today.toLocaleDateString("en", { weekday: "long", month: "long", day: "numeric", year: "numeric" });

  return (
    <div className="p-4 lg:p-6">
      <Tabs defaultValue="today">
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <TabsList>
            <TabsTrigger value="today">Today</TabsTrigger>
            <TabsTrigger value="week">Week</TabsTrigger>
            <TabsTrigger value="month">Month</TabsTrigger>
          </TabsList>
          <span className="text-xs text-muted-foreground">{dateStr}</span>
        </div>

        <TabsContent value="today"><TodayView /></TabsContent>
        <TabsContent value="week"><WeekView /></TabsContent>
        <TabsContent value="month"><MonthView /></TabsContent>
      </Tabs>
    </div>
  );
}
