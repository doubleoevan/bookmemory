import { apiRequest } from "@/api/client";

import { Link } from "react-router-dom";
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@bookmemory/ui";
import { CircleUserRoundIcon, LogOut } from "lucide-react";
import { useCurrentUser } from "@/features/authentication/hooks/useCurrentUser";
import { useTheme } from "@/app/theme";
import { logoutApiV1AuthLogoutPost } from "@bookmemory/contracts";

export default function UserMenu() {
  const { theme, setTheme } = useTheme();
  const { user } = useCurrentUser();

  const onChangeTheme = (theme: string) => {
    if (theme !== "light" && theme !== "dark") {
      return;
    }
    setTheme(theme);
  };

  const onLogout = async () => {
    try {
      await apiRequest(logoutApiV1AuthLogoutPost);
    } finally {
      // simplest + safest for cookie auth: force a clean reload
      window.location.href = "/login";
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="User Menu" className="rounded-full">
          {user?.picture_url ? (
            <Avatar className="h-8 w-8">
              <AvatarImage
                src={user.picture_url}
                alt={user.name ?? "User"}
                loading="lazy"
                decoding="async"
              />
              <AvatarFallback>
                <CircleUserRoundIcon className="h-8 w-8" />
              </AvatarFallback>
            </Avatar>
          ) : (
            <CircleUserRoundIcon className="h-8 w-8" />
          )}
          <span className="sr-only">User Menu</span>
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-56">
        {user?.picture_url && (
          <>
            <DropdownMenuItem>
              <Link to="/" className="flex items-center gap-2" aria-label="Go to home">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user.picture_url} alt={user.name ?? "User"} />
                  <AvatarFallback>
                    <CircleUserRoundIcon className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
                <span>{user.name}</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}

        <DropdownMenuLabel>Theme</DropdownMenuLabel>
        <DropdownMenuRadioGroup value={theme} onValueChange={onChangeTheme}>
          <DropdownMenuRadioItem value="light">Light</DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="dark">Dark</DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>

        {user && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer" onClick={onLogout}>
              <LogOut className="h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
