import { bookmarkHandlers } from "@/mocks/handlers/bookmarks";
import { tagHandlers } from "@/mocks/handlers/tags";
import { userHandlers } from "@/mocks/handlers/users";

export const handlers = [...bookmarkHandlers, ...tagHandlers, ...userHandlers];
