import { describe, it, expect, vi, beforeEach } from "vitest";
import { useAuraStore } from "@/stores/aura";
import { useMasterStore } from "@/stores/master";
import { useThemeStore } from "@/stores/theme";

beforeEach(() => {
  localStorage.clear();
  // Reset Zustand stores between tests
  useAuraStore.setState({ lastFlareCategory: null, flareSeq: 0 });
  useMasterStore.setState({ message: null });
  useThemeStore.setState({ theme: "dark" });
});

describe("useAuraStore", () => {
  it("starts with no flare", () => {
    const state = useAuraStore.getState();
    expect(state.lastFlareCategory).toBeNull();
    expect(state.flareSeq).toBe(0);
  });

  it("triggerFlare sets category and increments seq", () => {
    useAuraStore.getState().triggerFlare("stamina");
    const s1 = useAuraStore.getState();
    expect(s1.lastFlareCategory).toBe("stamina");
    expect(s1.flareSeq).toBe(1);

    useAuraStore.getState().triggerFlare("wellness");
    const s2 = useAuraStore.getState();
    expect(s2.lastFlareCategory).toBe("wellness");
    expect(s2.flareSeq).toBe(2);
  });
});

describe("useMasterStore", () => {
  it("starts with no message", () => {
    expect(useMasterStore.getState().message).toBeNull();
  });

  it("show sets the message", () => {
    useMasterStore.getState().show({ content: "Well done!", category: "intelligence" });
    const msg = useMasterStore.getState().message;
    expect(msg?.content).toBe("Well done!");
    expect(msg?.category).toBe("intelligence");
  });

  it("dismiss clears the message", () => {
    useMasterStore.getState().show({ content: "Hello", category: "stamina" });
    useMasterStore.getState().dismiss();
    expect(useMasterStore.getState().message).toBeNull();
  });

  it("auto-dismisses after 6 seconds", () => {
    vi.useFakeTimers();
    useMasterStore.getState().show({ content: "Temp", category: "creativity" });
    expect(useMasterStore.getState().message).not.toBeNull();

    vi.advanceTimersByTime(6000);
    expect(useMasterStore.getState().message).toBeNull();
    vi.useRealTimers();
  });
});

describe("useThemeStore", () => {
  it("defaults to dark theme", () => {
    expect(useThemeStore.getState().theme).toBe("dark");
  });

  it("toggle switches between dark and light", () => {
    useThemeStore.getState().toggle();
    expect(useThemeStore.getState().theme).toBe("light");

    useThemeStore.getState().toggle();
    expect(useThemeStore.getState().theme).toBe("dark");
  });

  it("set explicitly sets theme", () => {
    useThemeStore.getState().set("light");
    expect(useThemeStore.getState().theme).toBe("light");
    expect(localStorage.getItem("aura-theme")).toBe("light");
  });

  it("persists theme to localStorage on toggle", () => {
    useThemeStore.getState().toggle();
    expect(localStorage.getItem("aura-theme")).toBe("light");
  });
});
