import Link from "next/link";

export const NavBar = () => (
  <nav className="bg-green-700 text-white p-4 flex justify-between items-center">
    <div className="font-bold text-xl">CropEye Dashboard</div>
    <div className="space-x-4">
      <Link href="/">Dashboard</Link>
      <Link href="/images">Images</Link>
      <Link href="/analytics">Analytics</Link>
    </div>
  </nav>
);
