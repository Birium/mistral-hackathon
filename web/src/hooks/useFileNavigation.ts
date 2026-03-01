import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

export function useFileNavigation() {
  const navigate = useNavigate();

  const navigateToFile = useCallback(
    (path: string) => {
      navigate("/file/" + path);
    },
    [navigate],
  );

  return navigateToFile;
}
