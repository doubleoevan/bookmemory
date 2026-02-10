import { bookmarkHandlers } from "@/mocks/handlers/bookmarks";
import { summaryHandlers } from "@/mocks/handlers/summary";
import { tagHandlers } from "@/mocks/handlers/tags";
import { userHandlers } from "@/mocks/handlers/users";

export const handlers = [...bookmarkHandlers, ...summaryHandlers, ...tagHandlers, ...userHandlers];
