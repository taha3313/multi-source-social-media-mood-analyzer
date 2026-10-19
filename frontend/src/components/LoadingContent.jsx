export default function LoadingContent({ loading, component }) {
  return loading ? (
    <div role="status" className="my-4 h-32 animate-pulse rounded-lg bg-gray-100 dark:bg-gray-800">
      <span className="sr-only">Analyzing posts…</span>
    </div>
  ) : component;
}
