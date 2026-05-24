import { Outlet } from "react-router-dom";

import { useCountries } from "./api/queries";
import { Sidebar } from "./components/Sidebar";

export function App() {
  const { data: countries } = useCountries();

  return (
    <main className="app-shell">
      <Sidebar countries={countries ?? []} />
      <Outlet />
    </main>
  );
}
