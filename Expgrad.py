import numpy as np

class Model:

	def __init__(self, n_states, n_options, n_primitives):

		self.n_states = n_states
		self.n_options = n_options
		self.n_primitives = n_primitives

		self.eta = np.random.rand(n_states, n_options)
		self.phi = np.random.rand(n_states, n_options)
		self.pi = np.random.rand(n_options)
		self.b = np.random.rand(n_states, n_options, n_primitives)

		self.states = []
		self.prim = []

		self.alpha = None
		self.beta = None

		self.gamma = None
		self.xi = None

		self.likelihood = 0

		self.T = 0

		# normalize probabilities
		for s in range(n_states):

			for o in range(n_options):
				# self.a[s,o,:] = self.a[s,o,:]/sum(self.a[s,o,:])
				self.b[s,o,:] = self.b[s,o,:]/sum(self.b[s,o,:])

			self.eta[s] = self.eta[s]/np.sum(self.eta[s])

		self.pi = self.pi/sum(self.pi)

	# ADDING DATA

	def addData(self, packed_data):

		for s, a, _ in packed_data:
			self.states.append(s)
			self.prim.append(a)

		self.T += len(packed_data)

		self.alpha = np.zeros((self.T, self.n_options))
		self.beta = np.zeros((self.T, self.n_options))

		self.gamma = np.zeros((self.T, self.n_options))
		self.xi = np.zeros((self.T, self.n_options, self.n_options))


	# MODEL QUERIES

	def A(self, state):
		m = self.phi[state].reshape(self.n_options,1).dot(self.eta[state].reshape(1,self.n_options))
		np.fill_diagonal(m, 1-self.phi[state])
		return m

	def B(self, state):
		return self.b[state]

	def priors(self):
		return self.pi


	# FORWARD-BACKWARD PROBABILITIES

	def getForward(self):

		self.alpha[0] = self.priors()*self.B(self.states[0])[:,self.prim[0]]
		self.alpha[0] /= np.sum(self.alpha[0])

		for t in range(1,len(self.alpha)):
			transition_p = self.alpha[t-1].dot(self.A(self.states[t]))
			self.alpha[t] = transition_p*self.B(self.states[t])[:,self.prim[t]]

			if t==len(self.alpha)-1:
				self.likelihood = np.sum(self.alpha[t])

			self.alpha[t] /= np.sum(self.alpha[t])

		return self.alpha

	def getBackward(self):

		self.beta[-1] = np.ones((self.n_options))
		self.beta[-1] /= np.sum(self.beta[-1])

		for t in range(len(self.beta)-2, -1, -1):
			post_nxt = self.B(self.states[t+1])[:,self.prim[t+1]]*self.beta[t+1]
			self.beta[t] = self.A(self.states[t]).dot(post_nxt)

			self.beta[t] /= np.sum(self.beta[t])

		return self.beta


	# MARGINAL LIKELIHOODS

	def getOccurence(self):

		self.gamma = self.alpha*self.beta

		norm = 1/np.sum(self.gamma, axis=1)
		norm[~np.isfinite(norm)] = 0

		self.gamma = (self.gamma.transpose()*norm).transpose()
		return self.gamma

	def getCoOccurrence(self):

		for t in range(1, len(self.alpha)):

			margins = self.alpha[t-1].transpose().dot(self.beta[t])
			transitionP = self.A(self.states[t])*margins

			unnormed = self.B(self.states[t])[:,self.prim[t]]*transitionP

			norm = 1 / np.sum(unnormed, axis=1)
			norm[~np.isfinite(norm)] = 0

			self.xi[t] = (unnormed.transpose()*norm).transpose()

		return self.xi


	# UPDATE
	def EStep(self):

		self.getForward()
		self.getBackward()

		self.getOccurence()
		self.getCoOccurrence()

	def MStep(self):

		# Update transition probabilities
		numPhi = np.zeros((self.n_states, self.n_options)) + 1.e-07
		denPhi = np.zeros((self.n_states, self.n_options)) + 1.e-07

		for t in range(1, self.T):
			numPhi[self.states[t-1]] += self.xi[t].sum(axis=1)-np.diag(self.xi[t])
			denPhi[self.states[t]] += self.gamma[t]

		self.phi = numPhi/denPhi

		norm = 1 / np.sum(numPhi, axis=1)
		norm[~np.isfinite(norm)] = 0

		self.eta = (numPhi.transpose()*norm).transpose()

		# Update observation probabilities
		numB = np.zeros((self.n_states, self.n_options, self.n_primitives)) + 1.e-07
		denB = np.zeros((self.n_states, self.n_options)) + 1.e-07

		for t in range(self.T):
			numB[self.states[t], :, self.prim[t]] += self.gamma[t]
			denB[self.states] += self.gamma[t]

		self.b = (numB.transpose()/denB.transpose()).transpose()

		self.pi = self.eta[self.states[0]]

		# self.pi = self.gamma[0]

	def Start(self):

		self.EStep()

	def Step(self):

		self.MStep()
		self.EStep()

		return self.likelihood


	# SYSTEM

	def dump(self, fname):

		np.save(fname+"_A", self.a)
		np.save(fname+"_B", self.b)