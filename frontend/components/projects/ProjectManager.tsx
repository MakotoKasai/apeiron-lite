"use client";

import { useState } from "react";
import type { Project } from "@/types/Project"
import { ProjectList } from "./ProjectList";
import { ProjectForm} from "./ProjectForm";

type ProjectManagerProps = {
    initialProjects: Project[];
}

export function ProjectManager({initialProjects}: ProjectManagerProps) {
    const [projects, setProjects] = useState<Project[]>(initialProjects);

    function addProject(title: string, description: string) {
        const newProject: Project = {
            id: Date.now(),
            title,
            description,
        };
        setProjects([...projects, newProject]);
    }

    return (
        <>
            <ProjectForm onAdd={addProject} />
            <ProjectList projects={projects} />
        </>
    );
}