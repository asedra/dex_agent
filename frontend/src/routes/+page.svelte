<script lang="ts">
	import { onMount } from 'svelte';
	import CommandExecutor from '$lib/components/CommandExecutor.svelte';
	import SystemInfo from '$lib/components/SystemInfo.svelte';
	import BatchExecutor from '$lib/components/BatchExecutor.svelte';

	let activeTab = 'single';
	let apiToken = 'test_token_123';
	let apiUrl = 'http://localhost:8000';
	let isConnected = false;

	onMount(() => {
		// Load saved settings
		const savedToken = localStorage.getItem('apiToken');
		const savedUrl = localStorage.getItem('apiUrl');
		
		if (savedToken) apiToken = savedToken;
		if (savedUrl) apiUrl = savedUrl;
		
		// Test connection
		testConnection();
	});

	async function testConnection() {
		try {
			const response = await fetch(`${apiUrl}/`);
			isConnected = response.ok;
		} catch (error) {
			isConnected = false;
		}
	}

	function saveSettings() {
		localStorage.setItem('apiToken', apiToken);
		localStorage.setItem('apiUrl', apiUrl);
		testConnection();
	}
</script>

<svelte:head>
	<title>Windows PowerShell Agent</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow-sm border-b border-gray-200">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center py-6">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<h1 class="text-2xl font-bold text-gray-900">Windows PowerShell Agent</h1>
					</div>
				</div>
				<div class="flex items-center space-x-4">
					<div class="flex items-center space-x-2">
						<div class="w-3 h-3 rounded-full {isConnected ? 'bg-green-500' : 'bg-red-500'}"></div>
						<span class="text-sm text-gray-600">
							{isConnected ? 'Connected' : 'Disconnected'}
						</span>
					</div>
				</div>
			</div>
		</div>
	</header>

	<!-- Settings Panel -->
	<div class="bg-white border-b border-gray-200">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div>
					<label for="apiUrl" class="block text-sm font-medium text-gray-700">API URL</label>
					<input
						type="text"
						id="apiUrl"
						bind:value={apiUrl}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="http://localhost:8000"
					/>
				</div>
				<div>
					<label for="apiToken" class="block text-sm font-medium text-gray-700">API Token</label>
					<input
						type="password"
						id="apiToken"
						bind:value={apiToken}
						class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
						placeholder="Enter API token"
					/>
				</div>
				<div class="flex items-end">
					<button
						on:click={saveSettings}
						class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition duration-200"
					>
						Save Settings
					</button>
				</div>
			</div>
		</div>
	</div>

	<!-- Main Content -->
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Tab Navigation -->
		<div class="border-b border-gray-200 mb-8">
			<nav class="-mb-px flex space-x-8">
				<button
					class="py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'single' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					on:click={() => activeTab = 'single'}
				>
					Single Command
				</button>
				<button
					class="py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'batch' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					on:click={() => activeTab = 'batch'}
				>
					Batch Commands
				</button>
				<button
					class="py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'system' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					on:click={() => activeTab = 'system'}
				>
					System Info
				</button>
			</nav>
		</div>

		<!-- Tab Content -->
		{#if activeTab === 'single'}
			<CommandExecutor {apiUrl} {apiToken} />
		{:else if activeTab === 'batch'}
			<BatchExecutor {apiUrl} {apiToken} />
		{:else if activeTab === 'system'}
			<SystemInfo {apiUrl} {apiToken} />
		{/if}
	</div>
</div>
