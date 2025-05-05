import React from 'react';
import { Link } from 'react-router-dom';
import {
  PlusIcon,
  FolderIcon,
  CubeIcon,
  ArrowPathIcon,
  PuzzlePieceIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

// Sample data for demonstration
const recentProjects = [
  { id: '1', name: 'Sample Electronics Product', status: 'In Progress', updatedAt: '3 hours ago' },
  { id: '2', name: 'Fragile Glassware', status: 'Created', updatedAt: '1 day ago' },
];

const stats = [
  { name: 'Total Projects', value: '2', icon: FolderIcon, color: 'bg-indigo-100 text-indigo-600' },
  { name: '3D Models', value: '1', icon: CubeIcon, color: 'bg-green-100 text-green-600' },
  { name: 'Packaging Designs', value: '1', icon: PuzzlePieceIcon, color: 'bg-blue-100 text-blue-600' },
];

export default function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to VirtualPackaging. Your automated packaging design solution.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className={`flex-shrink-0 rounded-md p-3 ${stat.color}`}>
                  <stat.icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">{stat.name}</dt>
                    <dd>
                      <div className="text-lg font-medium text-gray-900">{stat.value}</div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="mb-8">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Link
            to="/projects/new"
            className="relative block rounded-lg border-2 border-dashed border-gray-300 p-4 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <PlusIcon className="mx-auto h-8 w-8 text-gray-400" />
            <span className="mt-2 block text-sm font-semibold text-gray-900">Create new project</span>
          </Link>
          <Link
            to="/projects/1/capture"
            className="relative block rounded-lg border-2 border-dashed border-gray-300 p-4 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <CubeIcon className="mx-auto h-8 w-8 text-gray-400" />
            <span className="mt-2 block text-sm font-semibold text-gray-900">Create 3D model</span>
          </Link>
        </div>
      </div>

      {/* Recent projects */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">Recent Projects</h2>
          <Link
            to="/projects"
            className="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            View all
          </Link>
        </div>
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul role="list" className="divide-y divide-gray-200">
            {recentProjects.map((project) => (
              <li key={project.id}>
                <Link to={`/projects/${project.id}`} className="block hover:bg-gray-50">
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <FolderIcon className="h-5 w-5 text-gray-400 mr-2" aria-hidden="true" />
                        <p className="text-sm font-medium text-blue-600 truncate">{project.name}</p>
                      </div>
                      <div className="ml-2 flex-shrink-0 flex">
                        <ChevronRightIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                      </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500">
                          Status: {project.status}
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <ArrowPathIcon
                          className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400"
                          aria-hidden="true"
                        />
                        <p>Updated {project.updatedAt}</p>
                      </div>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
            {recentProjects.length === 0 && (
              <li className="px-4 py-5 sm:px-6 text-center text-sm text-gray-500">
                No projects yet. <Link to="/projects/new" className="text-blue-600 hover:text-blue-500">Create your first project</Link>
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}