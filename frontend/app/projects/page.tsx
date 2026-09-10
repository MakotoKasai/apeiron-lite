import { ProjectManager } from "@/components/projects/ProjectManager"
import type { Project } from "@/types/Project";

const projects: Project[] = [
    {
        id: 1,
        title: "first project",
        description: "first description",
    },
    {
      id:2,
      title: "second project",
      description: "second description",
    },
];

export default function ProjectsPage() {
    return (
      <main>
          <h1>Projects</h1>
          <ProjectManager initialProjects = { projects } />
      </main>
    );
}