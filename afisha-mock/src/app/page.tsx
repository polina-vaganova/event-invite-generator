import EventCard from "@/components/EventCard";
import { getAllEvents } from "@/lib/store";

export default async function Home() {
  const events = await getAllEvents();

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <section className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
          Чем заняться в Москве
        </h1>
        <p className="mt-2 text-muted">
          Кино, концерты, спектакли и выставки. Нашли событие — позовите друга красивой
          открыткой.
        </p>
      </section>

      <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </section>
    </div>
  );
}
