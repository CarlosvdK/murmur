import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // Use getSession() instead of getUser() in middleware.
  // getSession() reads from the cookie locally (no network call),
  // so it can't hang. Route handlers should still use getUser()
  // for server-side validation when needed.
  let user = null;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    user = session?.user ?? null;
  } catch (e) {
    console.error("Middleware: auth check failed", e);
  }

  // Public routes that don't require auth
  const publicPaths = ["/", "/login", "/signup"];
  const isPublic =
    publicPaths.some((p) => request.nextUrl.pathname === p) ||
    request.nextUrl.pathname.startsWith("/auth/");

  if (!user && !isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }

  // If logged in and hitting login/signup, redirect to app
  if (
    user &&
    (request.nextUrl.pathname === "/login" ||
      request.nextUrl.pathname === "/signup")
  ) {
    const url = request.nextUrl.clone();
    url.pathname = "/app";
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}
