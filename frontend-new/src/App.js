import { Routes, Route } from "react-router-dom";
import Home from "./Home";
import Login from "./LoginPage";
import Profile from "./Profile";

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/profile" element={<Profile />}  />
    </Routes>
  );
}

export default AppRouter;
