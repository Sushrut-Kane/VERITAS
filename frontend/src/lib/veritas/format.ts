import { format, formatDistanceToNowStrict } from "date-fns";

export function formatTimestamp(value: string) {
  return format(new Date(value), "dd MMM yyyy · HH:mm:ss");
}

export function formatRelative(value: string) {
  return `${formatDistanceToNowStrict(new Date(value))} ago`;
}

export function formatConfidence(value: number) {
  return `${(value * 100).toFixed(0)}%`;
}

export function formatEvent(event: string) {
  return event.replace(/_/g, " ");
}
