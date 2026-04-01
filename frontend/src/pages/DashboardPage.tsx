import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useDashboardToday, useStats } from "@/hooks/useDashboard";
import { useAuraStore } from "@/stores/aura";
import AuraCanvas from "@/components/aura/AuraCanvas";
import StatsPanel from "@/components/dashboard/StatsPanel";
import QuestSection from "@/components/dashboard/QuestSection";
import TodayView from "@/components/dashboard/TodayView";
import WeekView from "@/components/dashboard/WeekView";
import MonthView from "@/components/dashboard/MonthView";

export default function DashboardPage() {
  const { data: stats } = useStats();
  const { data: todayData } = useDashboardToday();
  const { lastFlareCategory, flareSeq } = useAuraStore();
  const [tab, setTab] = useState("today");

  const scores = stats?.scores ?? todayData?.scores ?? {};
  const quests = todayData?.active_quests ?? [];
  const hasScores = Object.keys(scores).length > 0;

  return (
    <div className="relative min-h-[calc(100vh-56px)] p-5 lg:p-6">
      {/* Aura — dead center of the viewport, behind everything */}
      {hasScores && (
        <div
          className="pointer-events-none fixed z-0 hidden lg:block"
          style={{
            width: "600px",
            height: "600px",
            top: "50%",
            left: "calc(50% + 32px)",
            transform: "translate(-50%, -50%)",
          }}
        >
          <AuraCanvas scores={scores} flareCategory={lastFlareCategory} flareSeq={flareSeq} />
        </div>
      )}

      <Tabs value={tab} onValueChange={setTab}>
        <div className="relative z-10 mb-5">
          <TabsList>
            <TabsTrigger value="today">Today</TabsTrigger>
            <TabsTrigger value="week">Week</TabsTrigger>
            <TabsTrigger value="month">Month</TabsTrigger>
          </TabsList>
        </div>

        {/* Mobile: stacked */}
        {hasScores && (
          <div className="mb-5 lg:hidden">
            <AuraCanvas scores={scores} flareCategory={lastFlareCategory} flareSeq={flareSeq} />
          </div>
        )}

        {/* Desktop: [Habits] [Aura] [Stats] [Quests] */}
        <div className="relative z-10 grid gap-5 lg:grid-cols-[340px_1fr_200px_280px] xl:grid-cols-[400px_1fr_220px_320px] 2xl:grid-cols-[440px_1fr_240px_360px]">
          {/* Col 1: Habits */}
          <div className="space-y-5">
            <div className="lg:hidden">
              {hasScores && <StatsPanel scores={scores} />}
            </div>

            <TabsContent value="today" className="mt-0"><TodayView /></TabsContent>
            <TabsContent value="week" className="mt-0"><WeekView /></TabsContent>
            <TabsContent value="month" className="mt-0"><MonthView /></TabsContent>

            <div className="lg:hidden">
              <QuestSection quests={quests} />
            </div>
          </div>

          {/* Col 2: Aura breathing room */}
          <div className="hidden lg:block" />

          {/* Col 3: Stats (narrow column, near aura) */}
          <div className="hidden lg:block">
            {hasScores && <StatsPanel scores={scores} />}
          </div>

          {/* Col 4: Quests */}
          <div className="hidden lg:block">
            <QuestSection quests={quests} />
          </div>
        </div>
      </Tabs>
    </div>
  );
}
