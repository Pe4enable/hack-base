import React from "react";
import Link from "next/link";
import { DataGrid, GridColDef, GridRowsProp, GridToolbar } from "@mui/x-data-grid";
import type { NextPage } from "next";
import { InformationCircleIcon } from "@heroicons/react/24/outline";
import { MetaHeader } from "~~/components/MetaHeader";
import { sampleTableData } from "~~/utils/samples/tableData";

const Home: NextPage = () => {
  const rows: GridRowsProp = sampleTableData;

  const columns: GridColDef[] = [
    { field: "id", headerName: "ID", flex: 0.2 },
    { field: "title", headerName: "Project name", flex: 1 },
    { field: "short", headerName: "Short description", flex: 1 },
    { field: "date", headerName: "Date", flex: 0.5 },
    {
      field: "repo",
      headerName: "Repo link",
      flex: 0.5,
      renderCell: cell => {
        return (
          <a href={cell.value} target="_blank" rel="noreferrer" className="underline underline-offset-2">
            Repo...
          </a>
        );
      },
    },
    {
      field: "more",
      headerName: "More",
      flex: 0.2,
      renderCell: cell => {
        return (
          <Link
            href={`projects/${cell.id}`}
            passHref
            className={`hover:!text-neutral focus:!bg-secondary active:!text-neutral text-sm rounded-full inline-flex justify-center align-middle w-[30px] h-[30px] pt-1`}
          >
            <InformationCircleIcon className="h-5 w-5" />
          </Link>
        );
      },
    },
  ];

  return (
    <>
      <MetaHeader />
      <div className="flex items-center flex-col flex-grow pt-10">
        <div className="px-5 w-[90%]">
          <h1 className="text-center mb-6">
            <span className="block text-2xl mb-2">Database of submissions from crypto hackathons</span>
          </h1>
          <div className="flex flex-col items-center justify-center">
            <div className="w-full">
              <DataGrid rows={rows} columns={columns} slots={{ toolbar: GridToolbar }} />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Home;
