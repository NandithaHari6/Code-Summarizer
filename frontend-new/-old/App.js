import { Routes, Route } from "react-router-dom";
import Home from "./Home";
import Login from "./LoginPage";
import Profile from "./Profile";
import CodeSummary from "./CodeSummary";

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/profile" element={<Profile />}  />
      <Route path="/CodeSummary" element={<CodeSummary />} />
    </Routes>
  );
}

export default AppRouter;