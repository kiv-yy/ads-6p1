import { Outlet } from "react-router-dom";
import { Sidebar, BottomNav } from "../components/Navigation";
import { motion, AnimatePresence } from "motion/react";

export const MainLayout = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <main className="lg:ml-64 min-h-screen pb-20 lg:pb-0">
        <div className="max-w-6xl mx-auto p-4 md:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={window.location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
      <BottomNav />
    </div>
  );
};
