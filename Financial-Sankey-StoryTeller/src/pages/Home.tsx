import UploadForm from '../components/UploadForm';
import ProjectDescription from '../components/ProjectDescription';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-8 text-center text-white">
        Financial Sankey Story-Teller
      </h1>
      <ProjectDescription />
      <UploadForm />
    </div>
  );
}