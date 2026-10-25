export function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden rounded-3xl bg-gradient-to-br from-purple-500 via-indigo-500 to-blue-500 text-center shadow-2xl">
      <div className="pointer-events-none absolute -left-10 -top-10 h-72 w-72 rounded-full bg-purple-400 blur-3xl" />
      <h1
        className="bg-gradient-to-r from-fuchsia-400 to-indigo-400 bg-clip-text text-6xl text-transparent"
        style={{ fontFamily: "Inter, system-ui, sans-serif" }}
      >
        ✨ Unleash your potential
      </h1>
      <p className="rounded-2xl bg-gray-100 px-4 py-2 text-gray-400">
        Unlock the power of next-generation collaboration.
      </p>
      <div className="grid grid-cols-3 gap-6">
        <div className="rounded-2xl bg-white/10 p-6 shadow-xl backdrop-blur-md">
          <div className="rounded-2xl bg-white p-4 shadow-lg">
            <h3>🚀 Ship faster</h3>
            <p>Lorem ipsum dolor sit amet, your text here.</p>
          </div>
        </div>
        <div className="rounded-2xl bg-white/10 p-6 shadow-xl backdrop-blur-md">
          <h3>⚡ Feature Two</h3>
          <p>Elevate your workflow with a seamless experience.</p>
        </div>
        <div className="rounded-2xl bg-white/10 p-6 shadow-xl backdrop-blur-md">
          <h3>🎯 Feature Three</h3>
          <button className="rounded-full bg-indigo-600 px-4 py-2 text-white">Get Started</button>
        </div>
      </div>
    </section>
  );
}
