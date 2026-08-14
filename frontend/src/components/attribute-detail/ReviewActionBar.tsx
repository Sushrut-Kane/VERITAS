import { useNavigate } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { useReviewAction } from "@/lib/veritas/hooks";

type FormValues = { value: string; note: string };

export function ReviewActionBar({ id, currentValue }: { id: string; currentValue: string }) {
  const action = useReviewAction(id);
  const navigate = useNavigate();
  const { register, handleSubmit } = useForm<FormValues>({
    defaultValues: { value: currentValue, note: "" },
  });

  async function run(kind: "approve" | "reject" | "edit", values: FormValues) {
    try {
      await action.mutateAsync({
        action: kind,
        edited_value: kind === "edit" ? values.value : undefined,
        reviewer_note: values.note || undefined,
      });
      toast.success(kind === "reject" ? "Rejected" : kind === "edit" ? "Edited and published" : "Published");
      if (kind !== "edit") navigate({ to: "/review" });
    } catch (error) {
      toast.error("Review failed", { description: (error as Error).message });
    }
  }

  return (
    <section className="rounded-md border border-primary/30 bg-accent/40 p-5">
      <h2 className="text-sm font-medium uppercase tracking-[0.16em] text-muted-foreground">Your decision</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        Approve to publish this value as-is, edit it before publishing, or reject it outright.
      </p>

      <form className="mt-4 space-y-3" onSubmit={handleSubmit((v) => run("edit", v))}>
        <div className="flex flex-wrap gap-3">
          <label className="w-full flex-1 text-xs text-muted-foreground sm:w-auto">
            Value
            <input
              {...register("value")}
              className="data-value mt-1 w-full rounded-sm border bg-surface px-3 py-2 text-sm text-foreground"
            />
          </label>
          <label className="w-full flex-1 text-xs text-muted-foreground sm:w-auto">
            Note (optional)
            <input
              {...register("note")}
              placeholder="Why you decided this"
              className="mt-1 w-full rounded-sm border bg-surface px-3 py-2 text-sm text-foreground"
            />
          </label>
        </div>

        <div className="grid grid-cols-1 gap-2 sm:flex sm:flex-wrap">
          <button
            type="button"
            disabled={action.isPending}
            onClick={handleSubmit((v) => run("approve", v))}
            className="w-full rounded-sm bg-verified px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50 sm:w-auto sm:py-2"
          >
            Approve and publish
          </button>
          <button
            type="submit"
            disabled={action.isPending}
            className="w-full rounded-sm bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground disabled:opacity-50 sm:w-auto sm:py-2"
          >
            Save edit and publish
          </button>
          <button
            type="button"
            disabled={action.isPending}
            onClick={handleSubmit((v) => run("reject", v))}
            className="w-full rounded-sm border border-unsupported/40 bg-unsupported-soft px-4 py-2.5 text-sm font-medium text-unsupported disabled:opacity-50 sm:w-auto sm:py-2"
          >
            Reject
          </button>
        </div>
      </form>
    </section>
  );
}
