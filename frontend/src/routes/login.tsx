import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { useUiStore } from "@/lib/store/uiStore";

export const Route = createFileRoute("/login")({
  validateSearch: (search: Record<string, unknown>): { redirect?: string } => {
    const raw = search["redirect"];
    const value = typeof raw === "string" ? raw : undefined;
    // Only allow same-origin in-app paths.
    return value && value.startsWith("/") && !value.startsWith("//") ? { redirect: value } : {};
  },
  head: () => ({
    meta: [
      { title: "Sign in — VERITAS" },
      { name: "description", content: "Sign in to review and publish verified product attributes in VERITAS." },
      { property: "og:title", content: "Sign in — VERITAS" },
      { property: "og:description", content: "Reviewer access to the VERITAS verification workspace." },
    ],
  }),
  component: LoginPage,
});

type FormValues = { email: string; password: string };

const DEMO_EMAIL = "reviewer@veritas.dev";
const DEMO_PASSWORD = "veritas-demo";

function LoginPage() {
  const signIn = useUiStore((s) => s.signIn);
  const navigate = useNavigate();
  const { redirect } = Route.useSearch();
  const { register, handleSubmit, setValue, formState } = useForm<FormValues>({
    defaultValues: { email: "", password: "" },
  });

  return (
    <div className="mx-auto flex max-w-md flex-col justify-center px-4 py-16 sm:px-6 sm:py-24">
      <ShieldCheck className="h-6 w-6 text-primary" aria-hidden />
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">Sign in</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Demo access for reviewers. The session lives in memory only — no token is written to storage.
      </p>

      <div className="mt-6 rounded-sm border bg-surface p-4">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">Demo credentials</p>
        <dl className="mt-2 space-y-1 font-mono text-sm text-foreground">
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">email</dt>
            <dd>{DEMO_EMAIL}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">password</dt>
            <dd>{DEMO_PASSWORD}</dd>
          </div>
        </dl>
        <button
          type="button"
          onClick={() => {
            setValue("email", DEMO_EMAIL, { shouldValidate: true });
            setValue("password", DEMO_PASSWORD, { shouldValidate: true });
          }}
          className="mt-3 w-full rounded-sm border px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-accent"
        >
          Use demo credentials
        </button>
      </div>

      <form
        className="mt-6 space-y-4"
        onSubmit={handleSubmit((values) => {
          signIn(values.email);
          toast.success("Signed in", { description: values.email });
          // Navigate to dashboard or previous destination
          navigate({ to: redirect ?? "/dashboard", viewTransition: true, replace: true });
        })}
      >
        <label className="block text-xs text-muted-foreground">
          Email
          <input
            type="email"
            placeholder={DEMO_EMAIL}
            {...register("email", { required: true })}
            className="mt-1 w-full rounded-sm border bg-surface px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
          />
        </label>
        <label className="block text-xs text-muted-foreground">
          Password
          <input
            type="password"
            placeholder={DEMO_PASSWORD}
            {...register("password", { required: true })}
            className="mt-1 w-full rounded-sm border bg-surface px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
          />
        </label>
        <button
          type="submit"
          disabled={formState.isSubmitting}
          className="w-full rounded-sm bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
        >
          Sign in
        </button>
      </form>
    </div>
  );
}
