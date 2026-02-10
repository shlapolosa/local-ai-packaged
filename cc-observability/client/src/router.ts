import { createRouter, createWebHistory } from 'vue-router';

const ProjectsOverview = () => import('./pages/ProjectsOverview.vue');
const ProjectDetail = () => import('./pages/ProjectDetail.vue');
const ContributorDetail = () => import('./pages/ContributorDetail.vue');
const StoryDetail = () => import('./pages/StoryDetail.vue');
const CIODashboard = () => import('./pages/CIODashboard.vue');
const SessionTrace = () => import('./pages/SessionTrace.vue');

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'projects',
      component: ProjectsOverview,
    },
    {
      path: '/projects/:id',
      name: 'project-detail',
      component: ProjectDetail,
      props: true,
    },
    {
      path: '/contributors/:id',
      name: 'contributor-detail',
      component: ContributorDetail,
      props: true,
    },
    {
      path: '/stories/:id',
      name: 'story-detail',
      component: StoryDetail,
      props: true,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: CIODashboard,
    },
    {
      path: '/traces',
      name: 'traces',
      component: SessionTrace,
    },
  ],
});
