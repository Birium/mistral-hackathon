import { useLocation } from "react-router-dom";
import { Breadcrumb } from "./Breadcrumb";

export const BreadCrumbsLayout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation()
  // Derive the relative path from the URL: /file/some/path.md → some/path.md
  const path = location.pathname.replace(/^\/file\//, '').replace(/^\/folder\//, '')
  const segments = path.split('/').filter(Boolean)

  return (
    <>
      <div className='flex p-5 bg-background self-start sticky top-0 w-full'>
        <Breadcrumb segments={segments} />
      </div>
      {children}
    </>
  );
};
