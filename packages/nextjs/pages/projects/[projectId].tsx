import React from "react";
import { GetServerSideProps } from "next";
import { MetaHeader } from "~~/components/MetaHeader";
import { sampleTableData } from "~~/utils/samples/tableData";

type Project = {
  id: number;
  hackathon: string;
  title: string;
  more: string | null;
  repo: string | null;
  demo: string | null;
  video: string | null;
  winner: string | null;
  short: string | null;
  description: string | null;
  date: string | null;
};

type PageProps = {
  project: Project | null;
};

const ProjectPage = ({ project }: PageProps) => {
  if (!project) {
    return <div>Project not found</div>;
  }

  return (
    <>
      <MetaHeader />
      <div className="flex items-center flex-col flex-grow pt-10">
        <div className="px-5 w-[90%]">
          <h1 className="mb-3 text-3xl font-bold">{project.title}</h1>
          <div className="mb-10">{project.hackathon}</div>
          <div className="mb-10">{project.short}</div>
          <div className="mb-12 flex gap-2">
            {project.repo && (
              <a
                href={project.repo}
                target="_blank"
                rel="noreferrer"
                className="border-2 border-base-300 hover:bg-secondary hover:shadow-md focus:!bg-secondary active:!text-neutral py-1.5 px-3 text-sm rounded-full"
              >
                Source Code
              </a>
            )}
            {project.demo && (
              <a
                href={project.demo}
                target="_blank"
                rel="noreferrer"
                className="border-2 border-base-300 hover:bg-secondary hover:shadow-md focus:!bg-secondary active:!text-neutral py-1.5 px-3 text-sm rounded-full"
              >
                Demo
              </a>
            )}
          </div>
          <div className="mb-10 text-2xl font-bold">Project Description</div>
          <div>{project.description}</div>
        </div>
      </div>
    </>
  );
};

export const getServerSideProps: GetServerSideProps = async context => {
  const projectId = (context.params?.projectId as string).toLowerCase();

  return {
    props: {
      project: sampleTableData.find(item => item.id === +projectId) || null,
    },
  };
};

export default ProjectPage;
