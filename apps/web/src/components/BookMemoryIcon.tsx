import { cn } from "@bookmemory/ui";
import darkIconUrl from "@/assets/icons/bookmemory-dark.svg";
import lightIconUrl from "@/assets/icons/bookmemory-light.svg";
import { useTheme } from "@/providers/theme";

type BookMemoryIconProps = {
  className?: string;
  size?: number;
};

export function BookMemoryIcon({ className, size = 20 }: BookMemoryIconProps) {
  const { theme } = useTheme();
  const iconUrl = theme === "dark" ? darkIconUrl : lightIconUrl;
  return (
    <img
      src={iconUrl}
      width={size}
      height={size}
      className={cn("shrink-0", className)}
      alt=""
      aria-hidden="true"
      draggable={false}
    />
  );
}
