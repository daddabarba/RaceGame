import numpy as np

class Model:

	def __init__(self, n_states, n_options, n_primitives):

		self.n_states = n_states
		self.n_options = n_options
		self.n_primitives = n_primitives

		self.eta = np.random.rand(n_states, n_options)
		self.psi = np.random.rand(n_states, n_options)
		self.pi = np.random.rand(n_options)
		self.b = np.random.rand(n_states, n_options, n_primitives)

		self.IINV = 1 - np.eye(n_options)

		self.states = []
		self.prim = []

		self.alpha = None
		self.beta = None

		self.gamma = None
		self.xi = None

		self.likelihood = 0

		self.T = 0

		# normalize probabilities
		self.normProbs()

	def normProbs(self):

		for s in range(self.n_states):
			for o in range(self.n_options):
				self.b[s,o,:] = self.b[s,o,:]/sum(self.b[s,o,:])

		self.eta = (self.eta.transpose()/self.eta.sum(axis=1).transpose()).transpose()
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
		m = self.psi[state].reshape(self.n_options,1).dot(self.eta[state].reshape(1,self.n_options))
		np.fill_diagonal(m, 1-self.psi[state])
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

		# self.gamma = self.alpha*self.beta
		# self.gamma /= np.diag(self.alpha.dot(self.beta.transpose())).sum()

		self.gamma = self.xi.sum(axis=2)

		return self.gamma

	def getCoOccurrence(self):

		# norm = np.diag(self.alpha.dot(self.beta.transpose()))

		for t in range(1, len(self.alpha)):

			margins = self.alpha[t-1].transpose().dot(self.beta[t])
			transitionP = self.A(self.states[t])*margins

			self.xi[t] = self.B(self.states[t])[:,self.prim[t]]*transitionP
			# self.xi[t] /= norm[t]

			self.xi[t] /= self.xi[t].sum()

		return self.xi


	# UPDATE
	def EStep(self):

		self.getForward()
		self.getBackward()

		self.getCoOccurrence()
		self.getOccurence()

	def MStep(self):

		# Update transition probabilities
		numPsi = np.zeros((self.n_states, self.n_options)) + 1.e-07
		numEta = np.zeros((self.n_states, self.n_options)) + 1.e-07
		denPsi = np.zeros((self.n_states, self.n_options)) + 1.e-07
		denEta = np.zeros((self.n_states, self.n_options)) + 1.e-07

		for t in range(1, self.T):
			numPsi[self.states[t]] += self.xi[t].sum(axis=1)-np.diag(self.xi[t])
			denPsi[self.states[t]] += self.gamma[t]

			numEta[self.states[t]] += self.xi[t].sum(axis=0)-np.diag(self.xi[t])
			denEta[self.states[t]] += self.IINV.dot(self.gamma[t])

		self.psi = numPsi/denPsi
		self.eta = numEta/denEta

		# Update observation probabilities
		numB = np.zeros((self.n_states, self.n_options, self.n_primitives)) + 1.e-07
		denB = np.zeros((self.n_states, self.n_options)) + 1.e-07

		for t in range(self.T-1):
			numB[self.states[t], :, self.prim[t]] += self.gamma[t+1]
			denB[self.states] += self.gamma[t+1]

		self.b = (numB.transpose()/denB.transpose()).transpose()

		# Update priors
		self.pi = self.gamma[1]

	def Start(self):

		self.EStep()

	def Step(self):

		self.MStep()
		self.EStep()

		# self.normProbs()

		return self.likelihood


	# SYSTEM

	def dump(self, fname):

		np.save(fname+"_A", self.a)
		np.save(fname+"_B", self.b)