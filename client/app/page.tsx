"use client";
import { useRouter } from "next/navigation";
import React, { useEffect } from "react";
import { ROUTE_ADMIN } from "utils/constants";
import { useGetMe } from "@/hooks/useUsers";
import { Loader } from "@/components/loader/Loader";
import { toast } from "react-toastify";

const MainPage = () => {
  const router = useRouter();
  const { data: workspaceResponse, isLoading, isError } = useGetMe();
  const myDetails = workspaceResponse?.data;

  const handleSpaceClick = () => {
    localStorage.setItem("firstName", myDetails?.first_name);
    localStorage.setItem("email", myDetails?.email);
    localStorage.setItem("user_id", myDetails?.id);
    localStorage.setItem(
      "selectedOrganization",
      JSON.stringify(myDetails?.organizations[0])
    );
    localStorage.setItem("spaceId", myDetails?.space?.id);
    localStorage.setItem("spaceName", myDetails?.space?.name);
    router.push(ROUTE_ADMIN);
  };

  useEffect(() => {
    if (workspaceResponse?.data) {
      handleSpaceClick();
    }
    if (isError) {
      toast.error("Something went wrong fetching credentials!");
    }
  }, [workspaceResponse]);

  return (
    <>
      {isLoading && (
        <div className="flex items-center justify-center m-auto h-full w-full">
          <Loader />
        </div>
      )}
    </>
  );
};

export default MainPage;
