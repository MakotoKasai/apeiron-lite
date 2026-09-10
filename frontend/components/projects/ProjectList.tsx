import type { Project } from "@/types/Project";
import {ProjectCard} from "./ProjectCard";

type ProjectListProps = {
    projects: Project[];
}

export function ProjectList({projects}: ProjectListProps){
    return (
        <ul>
            {
                projects.map((project: Project) => (
                    <ProjectCard key={project.id} project={project} />
                ))
            }
        </ul>
    )

}